import java.rmi.Remote;
import java.rmi.RemoteException;

public interface CalculadoraInterfaz extends Remote {

    public double add(double par1, double par2) throws RemoteException;

    public double sub(double par1, double par2) throws RemoteException;

    public double mul(double par1, double par2) throws RemoteException;

    public double div(double par1, double par2) throws RemoteException;

    public double square(double par1) throws RemoteException;
}
