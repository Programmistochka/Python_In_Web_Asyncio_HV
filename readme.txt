����������� ���������� �� �������� ������ � ����� StarrWars � �� (����������� � ������� docker-compose �� ���� postgresql)

��� ������� ����������:
1. �������� ������������ ��������� � ������������ ����������� ��� �� (.env)
	python -m venv async_env
2. ������������ ����������� ��������� 
	async_env\Scripts\activate.bat
3. ���������� requirements.txt
	pip install -r requirements.txt
4. ��� ������������� ���������� �� �� Docker-���������� 
	docker-compose up
5. ��������� ���� ����������� � �� � models.py
	��� ������� ��� �� - 5432
	��� Docker ���������� � �� - 5431