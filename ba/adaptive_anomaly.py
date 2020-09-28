import logging
import math
from datetime import date

import numpy as np

import mvp.common.params as params
from mvp.common import errors
from mvp.common.db.tables.scoring import UserFeatures

from mvp.common.db.utils import DBSession, load_empl_feature_series
from mvp.scoring.features.general.general_feature import GeneralFeature

ANOMALY_LIKEHOOD = "anomaly_likehood"
ANOMALY_LIKEHOOD_LOG = "anomaly_likehood_log"
P_ALIAS = "_prob"


def _insert_features(feature_list, logger):
    """ Сохранить рассчитанные признаки в базу """

    if not feature_list:
        return

    for feature in feature_list:
        DBSession.add(feature)

    try:
        DBSession.commit()
        logger.info(f"{len(feature_list)} features saved to DB")
    except errors.DBError as ex:
        logger.exception(ex)
        DBSession.rollback()


def _update_features(feature_list, logger):
    """ Обновить заново рассчитанные признаки в базе """
    if not feature_list:
        return

    for feature in feature_list:
        DBSession.query(UserFeatures) \
            .filter(UserFeatures.activity_id == feature.activity_id,
                    UserFeatures.name == feature.name) \
            .update({UserFeatures.VALUE: feature.value},
                    synchronize_session=False)

    try:
        DBSession.commit()
        logger.info(f"{len(feature_list)} features updated in DB")
    except errors.DBError as ex:
        logger.exception(ex)
        DBSession.rollback()


def _delete_features(feature_list, logger):
    """ Удалить признаки из базы """
    if not feature_list:
        return

    for feature in feature_list:
        DBSession.query(UserFeatures) \
            .filter(UserFeatures.activity_id == feature.activity_id,
                    UserFeatures.name == feature.name) \
            .delete(synchronize_session=False)

    try:
        DBSession.commit()
        logger.info(f"{len(feature_list)} features deleted from DB")
    except errors.DBError as ex:
        logger.exception(ex)
        DBSession.rollback()


class AnomalyFeature(GeneralFeature):
    """ Признаки на базе данных об отпусках """

    def __init__(self, config):
        super(AnomalyFeature, self).__init__(config)
        self._supported_features = {
            ANOMALY_LIKEHOOD, ANOMALY_LIKEHOOD_LOG
        }

    def __call__(self, feature_name: str, start_date: date, end_date: date, employees: list, activities: dict):
        """ Метод для расчёта признаков """
        if feature_name not in self._supported_features:
            return [], [], []

        logger = logging.getLogger(self.__class__.__name__)

        config = self._config[params.FEATURES][feature_name]
        feature_list = list(config.get(params.BASE_FEATURES))

        feature_list = [name + P_ALIAS for name in feature_list]
        all_features = feature_list + [feature_name]
        feature_num = len(feature_list)
        n_e = 0
        for login in employees:
            features_for_insert = []
            features_for_update = []
            features_for_delete = []

            n_e += 1
            logger.info(f"Calcutaling for {login} {n_e}/{len(employees)}")
            features = load_empl_feature_series(all_features, [login], None, end_date)[login]
            for cur_date, slice in features.items():
                prev_likehood = slice.get(feature_name)
                if prev_likehood:
                    del slice[feature_name]
                if (len(slice) <= feature_num) & (len(slice) > 0):
                    if feature_name == ANOMALY_LIKEHOOD:
                        likehood = np.power(multiply.reduce(list(slice.values())),1/len(slice))
                    else:
                        likehood = np.power(sum(np.log(list(slice.values()))), 1/len(slice))
                    if prev_likehood != likehood:
                        feature_object = self._create_feature_object(
                            activities[login][cur_date][params.ACTIVITY_ID],
                            feature_name,
                            likehood
                        )
                        if prev_likehood is None:
                            if not math.isnan(likehood):
                                features_for_insert.append(feature_object)
                        elif likehood is None or math.isnan(likehood):
                            features_for_delete.append(feature_object)
                        elif abs((likehood - prev_likehood) / likehood) > 1e-13:
                            features_for_update.append(feature_object)

            _insert_features(features_for_insert, logger)
            _update_features(features_for_update, logger)
            _delete_features(features_for_delete, logger)

        return [], [], []

    @property
    def supported_features(self) -> set:
        """ Метод возвращает список поддерживаемых экстрактором признаков """
        return self._supported_features
