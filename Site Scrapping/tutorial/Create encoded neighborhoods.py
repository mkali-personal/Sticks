import urllib
l = [
                        '����',
                        '���-����',
                        '����-�������-����',
                        '����-���-����',
                        '�����-�-����',
                        '������-����',
                        '���-����',
                        '�����',
                        '���-���',
                        '������-������',
                        '�����-�����',
                        '����',
                        '�����-�-�',
                        '����',
                        '����-�����',
                        '��������-������',
                        '����-���-����',
                        '���-���',
                        '����-����',
                        '����-���',
                        '�������',
                        '����-�����',
                        '���-�����',
                        '��-���',
                        '����-����',
                        '�����-�������',
                        '����-���-����',
                        '�����',
                        '����-����',
                        '�����-�����',
                        '����-�����',
                        '�����-�-�',
                        '����-�����',
                        '�������',
                        '���-����',
                        '�����-����',
                        '���-�����',
                        '����-����',
                        '����',
                        '���-���',
                        '����-����',
                        '����-�����',
                        '����-���-����',
                        '��',
                        '���-�����',
                        '����-����',
                        '���-����',
                        '����-���-����',
                        '���-����',
                        '���-���',
                        '���-�����',
                        '�����',
                        '�����-���',
                        '�����',
                        '�����-������',
                        '����-���',
                        '�����',
                        '���-���',
                        '���-���-���-�',
                        '����-������-�����',
                        '�����-�',
                        '����-���',
                        '�����-�',
                        '�����-����',
                        '�����-��',
                        '�����',
                        '����',
                        '����-�����'
                        ]



l_p = []

for p in l:
    l_p.append(urllib.parse.quote(p))

l_p