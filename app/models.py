import uuid
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, UUID

db = SQLAlchemy()


class Organization(db.Model):
    """Organización a la que pertenece un autor."""

    __tablename__ = "organizations"

    organization_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relación inversa: autores que pertenecen a esta organización
    authors = db.relationship("Author", back_populates="organization", lazy="select")

    def to_dict(self):
        return {
            "organization_id": str(self.organization_id),
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Organization {self.name}>"


class PublicationType(db.Model):
    """Tipo de publicación (artículo, libro, tesis, etc.)."""

    __tablename__ = "publication_types"

    type_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relación inversa
    publications = db.relationship(
        "Publication", back_populates="publication_type", lazy="select"
    )

    def to_dict(self):
        return {
            "type_id": str(self.type_id),
            "type_name": self.type_name,
        }

    def __repr__(self):
        return f"<PublicationType {self.type_name}>"


# Tabla de asociación N:M entre Publication y Author
author_publication = db.Table(
    "author_publication",
    db.Column(
        "publication_id",
        UUID(as_uuid=True),
        db.ForeignKey("publications.publication_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "author_id",
        UUID(as_uuid=True),
        db.ForeignKey("authors.author_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Author(db.Model):
    """Autor de una publicación."""

    __tablename__ = "authors"

    author_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    orcid_url = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # FK a organización
    organization_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("organizations.organization_id", ondelete="SET NULL"),
        nullable=True,
    )
    organization = db.relationship("Organization", back_populates="authors")

    # Relación N:M con Publication
    publications = db.relationship(
        "Publication",
        secondary=author_publication,
        back_populates="authors",
        lazy="select",
    )

    def to_dict(self):
        return {
            "author_id": str(self.author_id),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "orcid_url": self.orcid_url,
            "country": self.country,
            "organization": self.organization.to_dict() if self.organization else None,
        }

    def __repr__(self):
        return f"<Author {self.first_name} {self.last_name}>"


class Publication(db.Model):
    """Publicación del sistema editorial."""

    __tablename__ = "publications"

    publication_id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title = db.Column(db.String(500), nullable=False)
    publish_date = db.Column(db.DateTime(timezone=True), nullable=True)
    resource_url = db.Column(db.String(500), nullable=True)

    # Array nativo de PostgreSQL para las palabras clave
    keywords = db.Column(ARRAY(db.String), nullable=True, default=list)

    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # FK al tipo de publicación
    type_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("publication_types.type_id", ondelete="SET NULL"),
        nullable=True,
    )
    publication_type = db.relationship("PublicationType", back_populates="publications")

    # Relación N:M con Author
    authors = db.relationship(
        "Author",
        secondary=author_publication,
        back_populates="publications",
        lazy="select",
    )

    def to_dict(self):
        return {
            "publication_id": str(self.publication_id),
            "title": self.title,
            "publish_date": (
                self.publish_date.isoformat() if self.publish_date else None
            ),
            "resource_url": self.resource_url,
            "keywords": self.keywords or [],
            "publication_type": (
                self.publication_type.to_dict() if self.publication_type else None
            ),
            "authors": [a.to_dict() for a in self.authors],
        }

    def __repr__(self):
        return f"<Publication {self.title}>"
