"""src column added for social auth

Revision ID: 5377a56e4d30
Revises: b2a3584e79a0
Create Date: 2024-08-01 13:24:28.218219

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5377a56e4d30'
down_revision = 'b2a3584e79a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category_course_association', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])

    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['_to'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['_from'], ['id'])

    with op.batch_alter_table('content', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'topic', ['topic_id'], ['id'])

    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'category', ['category_id'], ['id'])

    with op.batch_alter_table('course_tag_association', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])
        batch_op.create_foreign_key(None, 'tag', ['tag_id'], ['id'])

    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])

    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user'], ['id'])
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['recipient_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['sender_id'], ['id'])

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])
        batch_op.create_foreign_key(None, 'lesson', ['lesson_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('src', sa.String(length=50), nullable=True))

    with op.batch_alter_table('user_course_association', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'course', ['course_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user_role_association', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'role', ['role_id'], ['id'])

    with op.batch_alter_table('user_topic_progress', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'topic', ['topic_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_topic_progress', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('user_role_association', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('user_course_association', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('src')

    with op.batch_alter_table('topic', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('enrollment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('course_tag_association', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('content', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('category_course_association', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###