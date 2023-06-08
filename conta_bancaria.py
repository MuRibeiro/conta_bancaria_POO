from abc import ABC, abstractproperty, abstractclassmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        execedeu_saldo = valor > saldo

        if execedeu_saldo:
            print('\n *** ERRO! VOCÊ NÃO TEM SALDO SUFICIENTE ***')

        elif valor > 0:
            self._saldo -= valor
            print('\n *** SAQUE REALIZADO COM SUCESSO! ***')
            return True

        else:
            print('\n *** ERRO! VALOR INFORMADO É INVÁLIDO! ***')

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('\n *** DEPÓSITO REALIZADO COM SUCESSO ***')

        else:
            print('\n *** ERRO! VALOR INFORMADO É INVÁLIDO. ***')
            return False

        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacao if transacao['tipo'] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print('\n *** ERRO! O VALOR DO SAQUE EXCEDE O LIMITE! ***')

        elif excedeu_saques:
            print('\n *** ERRO! VOCÊ ATINGIU O LIMITE DE SAQUES DIÁRIO! ***')

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f'''
            Agência: \t{self.agencia}
            C/C: \t\t{self.numero}
            Titular: \t{self.cliente.nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
                'data': datetime.now().strftime
                ('%d-%m-%Y %H:%M:%s'),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = f'''\n
                                ============================
                                =      BANCO - PYTHON      =
                                ============================
                                = 1 - \tDEPÓSITO           =
                                = 2 - \tSAQUE              =
                                = 3 - \tEXTRATO            =
                                = 4 - \tNOVA CONTA         =
                                = 5 - \tLISTAR CONTAS      =
                                = 6 - \tNOVO USUÁRIO       =
                                = 0 - \tSAIR               =
                                ============================
    '''
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print('\n *** CLIENTE NÃO POSSUI CONTA! ***')
        return
    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\n *** CLIENTE NÃO ENCONTRADO! ***')
        return

    valor = float(input('Informe o valor do depósito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\n *** CLIENTE NÃO ENCONTRADO! ***')
        return

    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\n *** CLIENTE NÃO ENCONTRADO! ***')
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print('===============================================')
    print('                    EXTRATO         ')
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas movimentações!'
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print('===============================================')

def criar_cliente(clientes):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\n *** CLIENTE NÃO ENCONTRADO! ***')
        return

    nome = input('Informe o nome completo: ')
    data_nascimento = input('Informe a daata de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço (logradouro, n - bairro - cidade/sigla estado): ')

    cliente = PessoaFisica(nome=nome,data_nascimento=data_nascimento,cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print('*** CLIENTE CADASTRADO COM SUCESSO ***')

def criar_conta(numero_conta, clientes, contas):
    cpf = input('Informe o CPF do cliente: ')
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print('\n *** CLIENTE NÃO ENCONTRADO! ***')
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print('\n *** CONTA CRIADA COM SUCESSO! ***')

def listar_contas(contas):
    for conta in contas:
        print('=' * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == '1':
            depositar(clientes)

        elif opcao == '2':
            sacar(clientes)

        elif opcao == '3':
            exibir_extrato(clientes)

        elif opcao == '4':
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == '5':
            listar_contas(contas)

        elif opcao == '6':
            criar_cliente(clientes)

        elif opcao == '7':
            break

        else:
            print('*** ERRO! FAVOR SELECIONE UMA OPERAÇÃO VÁLIDA *** ')

main()


