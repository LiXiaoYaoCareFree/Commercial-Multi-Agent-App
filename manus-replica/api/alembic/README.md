```shell
cd .. && alembic revision --autogenerate -m "create demos table"
```

```shell
cd .. && alembic upgrade head
```

```shell
cd .. && alembic downgrade -1
```
