import java.rmi.RemoteException;

public class CalculadoraImplement implements CalculadoraInterfaz {

    public double add(double par1, double par2) throws RemoteException {
        return par1 + par2;
    }

    public double sub(double par1, double par2) throws RemoteException {
        return par1 - par2;
    }

    public double mul(double par1, double par2) throws RemoteException {
        return par1 * par2;
    }

    public double div(double par1, double par2) throws RemoteException {
        return par1 / par2;
    }

    public double square(double par1) throws RemoteException {
        return par1 * par1;
    }
}
