import binascii
import enum
from typing import List

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, BigInteger, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class DrmType(enum.Enum):
    local = 0
    mbind = 1


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    titles: List['Title'] = relationship('Title', back_populates='product')

    def __repr__(self):
        return "<Product(id='{}', name='{}', titles='\n{}')>".format(
            self.id, self.name,
            ''.join(''.join('\t' + y for y in x.__repr__().splitlines(True)) + '\n' for x in self.titles)
        )


class Title(Base):
    __tablename__ = 'title'

    id = Column(String(9), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))

    name = Column(String)
    update_info_url = Column(String)

    names: List['TitleName'] = relationship('TitleName', back_populates='title')
    update_info_urls: List['TitleUpdateInfoUrl'] = relationship('TitleUpdateInfoUrl', back_populates='title')
    product: Product = relationship('Product', back_populates='titles')
    updates: List['Update'] = relationship('Update', back_populates='title')

    def __repr__(self):
        return "<Title(id='{}', product_id='{}', updates='\n{}')>".format(
            self.id, self.product.id,
            ''.join(''.join('\t' + y for y in x.__repr__().splitlines(True)) + '\n' for x in self.updates)
        )


class TitleName(Base):
    __tablename__ = 'title_name'

    id = Column(Integer, primary_key=True)
    title_id = Column(String(9), ForeignKey('title.id'))
    language_id = Column(Integer, ForeignKey('language.id'))

    name = Column(String)

    title: Title = relationship('Title', back_populates='names')
    language: 'Language' = relationship('Language')

    def __repr__(self):
        return "<TitleName(id='{}', name='{}', title_id='{}', language='\n\t{}\n')".format(
            self.id, self.name, self.title.id, self.language
        )


class TitleUpdateInfoUrl(Base):
    __tablename__ = 'title_update_info_url'

    id = Column(Integer, primary_key=True)
    title_id = Column(String(9), ForeignKey('title.id'))
    language_id = Column(Integer, ForeignKey('language.id'))

    url = Column(String)

    title: Title = relationship('Title', back_populates='update_info_urls')
    language: 'Language' = relationship('Language')

    def __repr__(self):
        return "<TitleUpdateInfoUrl(id='{}', url='{}', title_id='{}', language='\n\t{}\n')".format(
            self.id, self.url, self.title.id, self.language
        )


class Language(Base):
    __tablename__ = 'language'

    id = Column(Integer, primary_key=True)
    name = Column(String, default='Unknown')

    def __repr__(self):
        return "<Language(id='{}', name='{}')".format(
            self.id, self.name
        )


class Update(Base):
    __tablename__ = 'update'

    id = Column(Integer, primary_key=True)
    title_id = Column(String(9), ForeignKey('title.id'))

    version = Column(Float)
    ps3_system_ver = Column(Float)

    title: Title = relationship('Title', back_populates='updates')
    update_packages: List['UpdatePackage'] = relationship('UpdatePackage', back_populates='update')

    def __repr__(self):
        return "<Update(id='{}', version='{}', ps3_system_ver='{}', update_packages='\n{}')>".format(
            self.id, self.version, self.ps3_system_ver,
            ''.join(''.join('\t' + y for y in x.__repr__().splitlines(True)) + '\n' for x in self.update_packages)
        )


class UpdatePackage(Base):
    __tablename__ = 'update_package'

    id = Column(Integer, primary_key=True)
    update_id = Column(Integer, ForeignKey('update.id'))

    url = Column(String)
    size = Column(BigInteger)
    sha1sum = Column(LargeBinary(20))
    drm_type = Column(Enum(DrmType))

    update: Update = relationship('Update', back_populates='update_packages')

    def __repr__(self):
        return "<UpdatePackage(id='{}', url='{}', size='{}', sha1sum='{}', drm_type='{}', update_id='{}')>".format(
            self.id, self.url, self.size, binascii.hexlify(self.sha1sum), self.drm_type, self.update.id
        )
