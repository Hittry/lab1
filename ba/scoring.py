import json

from sqlalchemy import Column, Date, DateTime, Integer, Float, String, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint

from mvp.common import utils as common_utils
from mvp.common.db.tables.ad import Employees, EMPLOYEES_TABLE, FK_FORMAT

Base = declarative_base()

ID = "id"


class UserForecasting(Base):
    """ Таблица ежедневной активности пользователей """

    ID = "id"
    LOGIN = "login"
    FORECAST_PERIOD = "forecast_period"
    FORECAST_WINDOW = "forecast_window"
    DISMISSAL_SETUP = "dismissal_setup"


    __tablename__ = "user_forecasting"
    __table_args__ = (UniqueConstraint(
        LOGIN, FORECAST_PERIOD, name=f"uq_{__tablename__}_{LOGIN}_{FORECAST_PERIOD}"), )

    id = Column(ID, BigInteger, primary_key=True, autoincrement=True)
    login = Column(LOGIN, String, nullable=False, index=True)
    forecast_period = Column(FORECAST_PERIOD, Integer, nullable=False)
    forecast_window = Column(FORECAST_WINDOW, Integer, nullable=False)
    dismissal_setup = Column(DISMISSAL_SETUP, Integer, nullable=False)
    ForeignKeyConstraint([login], [Employees.login],
                         name=FK_FORMAT.format(EMPLOYEES_TABLE, LOGIN),
                         onupdate="CASCADE",
                         ondelete="CASCADE")


class UserActivity(Base):
    """ Таблица ежедневной активности пользователей """

    ID = "id"
    LOGIN = "login"
    DAY_DATE = "day_date"

    __tablename__ = "user_activity"
    __table_args__ = (UniqueConstraint(
        LOGIN, DAY_DATE, name=f"uq_{__tablename__}_{LOGIN}_{DAY_DATE}"), )

    id = Column(ID, BigInteger, primary_key=True, autoincrement=True)
    login = Column(LOGIN, String, nullable=False)
    day_date = Column(DAY_DATE, Date, nullable=False, index=True)
    ForeignKeyConstraint([login], [Employees.login],
                         name=FK_FORMAT.format(EMPLOYEES_TABLE, LOGIN),
                         onupdate="CASCADE",
                         ondelete="CASCADE")


class UserAnomaly(Base):
    """ Таблица аномалий поведения сотрудников """

    ID = "id"
    SET_ID = "set_id"
    LOGIN = "login"
    DAY_DATE = "day_date"

    __tablename__ = "user_anomaly"
    __table_args__ = (UniqueConstraint(
        SET_ID, LOGIN, DAY_DATE, name=f"uq_{__tablename__}_{SET_ID}_{LOGIN}_{DAY_DATE}"), )

    id = Column(ID, BigInteger, primary_key=True, autoincrement=True)
    set_id = Column(SET_ID, Integer, nullable=False, index=True)
    login = Column(LOGIN, String, nullable=False)
    day_date = Column(DAY_DATE, Date, nullable=False)

class AnomalyExplain(Base):
    """Таблица с объяснениями аномалий"""

    ID = "id"
    MODEL_INFO_ID = "model_info_id"
    ACTIVITY_ID = "activity_id"
    ORDER = "order"
    DESCR = "descr"
	
    __tablename__ = "user_score_explanation"
    __table_args__ = (UniqueConstraint(
        ACTIVITY_ID, name=f"uq_{__tablename__}_{ACTIVITY_ID}"), )
	
    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    model_info_id = Column(MODEL_INFO_ID, BigInteger, nullable=False)
    activity_id = Column(ACTIVITY_ID, BigInteger, nullable=False)
    order = Column(ORDER, BigInteger, nullable = False)
    descr = Column(DESCR, String , nullable = False)
    ForeignKeyConstraint([activity_id], [UserActivity.id],
                         name=FK_FORMAT.format(UserActivity.__tablename__, ID),
                         onupdate="CASCADE",
                         ondelete="CASCADE")
    ForeignKeyConstraint([model_info_id], [ModelsInfo.id],
                         name=FK_FORMAT.format(ModelsInfo.__tablename__,
                                               ModelsInfo.id),
                         onupdate="CASCADE",
                         ondelete="CASCADE")
	

class UserFeatures(Base):
    """ Таблица с рассчитанными признаками для каждого пользователя """

    ACTIVITY_ID = "activity_id"
    NAME = "name"
    VALUE = "value"

    __tablename__ = "user_features"
    __table_args__ = (UniqueConstraint(
        NAME, ACTIVITY_ID, name=f"uq_{__tablename__}_{NAME}_{ACTIVITY_ID}"), )

    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    name = Column(NAME, String, nullable=False, index=True)
    value = Column(VALUE, Float, nullable=True)
    activity_id = Column(ACTIVITY_ID, BigInteger, nullable=False)
    ForeignKeyConstraint([activity_id], [UserActivity.id],
                         name=FK_FORMAT.format(UserActivity.__tablename__,
                                               UserActivity.ID),
                         onupdate="CASCADE",
                         ondelete="CASCADE")


class ModelsInfo(Base):
    """ Информация о созданных моделях """

    TIMESTAMP = "timestamp"
    MODEL_NAME = "model_name"
    MODEL_PARAMS = "model_params"
    USR_COLLECTION = "usr_collection"
    MODEL_HASH = "model_hash"
    FEATURE_NAMES = "feature_names"

    __tablename__ = "model_info"
    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    ts = Column(TIMESTAMP, DateTime, nullable=False)
    model_name = Column(MODEL_NAME, String, nullable=False)
    model_params = Column(MODEL_PARAMS, JSON, nullable=False)
    usr_collection = Column(USR_COLLECTION, JSON, nullable=False)
    feature_names = Column(FEATURE_NAMES, JSON, nullable=False)
    model_hash = Column(MODEL_HASH, String, nullable=False)

    @staticmethod
    def data_to_jstr(data):
        """ Преобразовать данные в json-строку """
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            data = sorted(data)
        elif not isinstance(data, dict):
            msg = f"Can't convert data of type {type(data)} to json-str"
            raise ValueError(msg)

        return json.dumps(data, separators=(',', ':'), sort_keys=True)

    def compute_hash(self):
        """ Рассчитать хэш-функцию на основании
         выборки пользователей и значений параметров модели """

        usr_collection_str = ModelsInfo.data_to_jstr(self.usr_collection)
        feature_names_str = ModelsInfo.data_to_jstr(self.feature_names)
        model_params_str = ModelsInfo.data_to_jstr(self.model_params)

        self.model_hash = common_utils.get_str_digest("%s%s%s%s" % (self.model_name, model_params_str,
                                                      usr_collection_str, feature_names_str))
        return self.model_hash


class UserScores(Base):
    """ Насчитанный скоринг пользователей """

    SCORE = "score"
    MODEL_INFO_ID = "model_info_id"
    ACTIVITY_ID = "activity_id"

    __tablename__ = "user_scores"
    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    model_info_id = Column(MODEL_INFO_ID, BigInteger, nullable=False)
    score = Column(SCORE, Float, nullable=False)
    activity_id = Column(ACTIVITY_ID, BigInteger, nullable=False)
    ForeignKeyConstraint([activity_id], [UserActivity.id],
                         name=FK_FORMAT.format(UserActivity.__tablename__, ID),
                         onupdate="CASCADE",
                         ondelete="CASCADE")
    ForeignKeyConstraint([model_info_id], [ModelsInfo.id],
                         name=FK_FORMAT.format(ModelsInfo.__tablename__,
                                               ModelsInfo.id),
                         onupdate="CASCADE",
                         ondelete="CASCADE")


class UsrScorePrediction(Base):
    """ Таблица для предсказания подсчета скоринга """
    USR_NAME = "usr_name"
    LOW_SC_PREDICTION_DATE = "low_sc_pred_date"
    MEAN_SC_PREDICTION_DATE = "mean_sc_pred_date"
    HIGH_SC_PREDICTION_DATE = "high_sc_pred_date"
    SC_LOAD_PERC = "sc_load_percent"

    __tablename__ = "user_score_prediction"
    id = Column(ID, Integer, primary_key=True)
    usr_name = Column(USR_NAME, String, nullable=False)
    low_sc_pred_date = Column(LOW_SC_PREDICTION_DATE, Date, nullable=False)
    mean_sc_pred_date = Column(MEAN_SC_PREDICTION_DATE, Date, nullable=False)
    high_sc_pred_date = Column(HIGH_SC_PREDICTION_DATE, Date, nullable=False)
    sc_load_percent = Column(SC_LOAD_PERC, Float, nullable=False)

    # TODO: После оптимизации структуры бд
    # ForeignKeyConstraint([empl_guid], [Employees.guid],
    #                      name=FK_FORMAT.format(Employees.__tablename__, Employees.guid),
    #                      onupdate="CASCADE", ondelete="CASCADE")


class ModelEvaluations(Base):
    """ Информация о созданных моделях """

    TIMESTAMP = "timestamp"

    __tablename__ = "model_evaluations"
    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    timestamp = Column(TIMESTAMP, DateTime, nullable=False)


class ModelMarks(Base):
    """ Информация о созданных моделях """

    ID = "id"
    EVALUATION_ID = "evaluation_id"
    MODEL_NAME = "model_name"
    MODEL_DESCRIPTION = "model_description"
    COLLECTION_NAME = "collection_name"
    COLLECTION_DESCRIPTION = "collection_description"
    THRESHOLD = "threshold"
    PRECISION = "precision"
    PRECISION_STD = "precision_std"
    RECALL = "recall"
    RECALL_STD = "recall_std"
    F_MEASURE = "f_measure"
    F_MEASURE_STD = "f_measure_std"
    TPR = "tpr"
    TPR_STD = "tpr_std"
    FPR = "fpr"
    FPR_STD = "fpr_std"
    ROC_AUC = "roc_auc"
    ROC_AUC_STD = "roc_auc_std"
    FIRED_VS_EMPLS = "fired_vs_empls"
    SLICES_PROP = "slices_prop"

    __tablename__ = "model_marks"
    id = Column(ID, Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(EVALUATION_ID, Integer, nullable=False)
    ForeignKeyConstraint((evaluation_id,), [ModelEvaluations.id],
                         name=FK_FORMAT.format(ModelEvaluations.__tablename__, ID),
                         onupdate="CASCADE",
                         ondelete="CASCADE")
    model_name = Column(MODEL_NAME, String, nullable=False)
    model_description = Column(MODEL_DESCRIPTION, String, nullable=True)
    collection_name = Column(COLLECTION_NAME, String, nullable=False)
    collection_description = Column(COLLECTION_DESCRIPTION, String, nullable=True)
    threshold = Column(THRESHOLD, Float, nullable=True)
    precision = Column(PRECISION, Float, nullable=True)
    precision_std = Column(PRECISION_STD, Float, nullable=True)
    recall = Column(RECALL, Float, nullable=True)
    recall_std = Column(RECALL_STD, Float, nullable=True)
    f_measure = Column(F_MEASURE, Float, nullable=True)
    f_measure_std = Column(F_MEASURE_STD, Float, nullable=True)
    tpr = Column(TPR, Float, nullable=True)
    tpr_std = Column(TPR_STD, Float, nullable=True)
    fpr = Column(FPR, Float, nullable=True)
    fpr_std = Column(FPR_STD, Float, nullable=True)
    roc_auc = Column(ROC_AUC, Float, nullable=True)
    roc_auc_std = Column(ROC_AUC_STD, Float, nullable=True)
    fired_vs_empls = Column(FIRED_VS_EMPLS, String, nullable=True)
    slices_prop = Column(SLICES_PROP, String, nullable=True)
