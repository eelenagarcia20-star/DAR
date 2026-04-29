import java.rmi.Remote;
import java.rmi.RemoteException;

public interface CirculoInterfaz extends Remote{

    public void setRadio (double valorRadio) throws RemoteException;

    public double getArea () throws RemoteException;

}
