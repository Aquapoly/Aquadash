from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models, schemas

def ensure_notification_columns(db: Session):
    engine = db.get_bind()
    inspector = inspect(engine)
    try:
        cols_list = inspector.get_columns("notifications")
        cols = {c["name"] for c in cols_list}
        cols_info = {c["name"]: c for c in cols_list}
    except Exception:
        models.Notification.__table__.create(bind=engine, checkfirst=True)
        return

    # TODO: delete once there is no more old schema (with message instead of description) in the wild
    if "message" in cols and "description" not in cols:
        db.execute(text('ALTER TABLE notifications RENAME COLUMN "message" TO "description";'))
        db.commit()

        cols_list = inspector.get_columns("notifications")
        cols = {c["name"] for c in cols_list}
        cols_info = {c["name"]: c for c in cols_list}
    if "message" in cols and "description" in cols:
        try:
            nullable = cols_info.get("message", {}).get("nullable", True)
        except Exception:
            nullable = True
        if nullable is False:
            db.execute(text('ALTER TABLE notifications ALTER COLUMN "message" DROP NOT NULL;'))
            db.commit()


    stmts = []
    if "description" not in cols:
        stmts.append('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS "description" TEXT;')
    if "level" not in cols:
        stmts.append('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS "level" TEXT;')
    if "read" not in cols:
        stmts.append('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS "read" BOOLEAN DEFAULT FALSE;')
    if "dismissed" not in cols:
        stmts.append('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS "dismissed" BOOLEAN DEFAULT FALSE;')
    if "timestamp" not in cols:
        stmts.append('ALTER TABLE notifications ADD COLUMN IF NOT EXISTS "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT now();')

    if stmts:
        for s in stmts:
            db.execute(text(s))
        db.commit()


# Crée une notification générique dans la base de données.
def post_notification(db: Session, description: str, level: schemas.NotificationLevel = schemas.NotificationLevel.info):
    # Make sure the notifications table has the expected columns before inserting.
    ensure_notification_columns(db)

    db_notification = models.Notification(description=description, level=level)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


# Récupère les notifications depuis la base.
# get_notifications = ca retourne liste des notif non lues so ca va nous etre utile quand
#                       on voudra genre mettre les notifs dans le dashbord ou wtv
def get_notifications(db: Session, only_unread: bool = False):
    # Ensure the notifications table has the expected columns before querying.
    ensure_notification_columns(db)

    query = models.__table__ if False else None  # placeholder to satisfy linters if needed
    query = None
    from sqlalchemy import select
    query = select(models.Notification).order_by(models.Notification.timestamp.desc())
    # The model stores a boolean `read` column (and `dismissed`) — return only not-read and not-dismissed
    if only_unread:
        from sqlalchemy import and_
        query = query.where(and_(models.Notification.read == False, models.Notification.dismissed == False))
    return db.execute(query).scalars().all()


# Marque une notification comme lue.
# mark_notification_as_read = on va appeler cette fonction quand on voudra que la notif soient efface genre
#                               avec un bouton X ou read ou wtv dans la page
def mark_notification_as_read(db: Session, notif_id: int):
    # Ensure the notifications table has the expected columns before updating.
    ensure_notification_columns(db)

    from sqlalchemy import update
    query = (
        update(models.Notification)
        .where(models.Notification.id == notif_id)
        .values(read=True)
        .returning(models.Notification)
    )
    notif = db.execute(query).scalars().first()
    db.commit()

    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notif_id} not found"
        )

    return notif
