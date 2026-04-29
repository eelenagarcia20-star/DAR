import java.rmi.RemoteException;

public class CirculoImplement implements CirculoInterfaz {

    private static double PI=Math.PI;
    private double radio;

    public CirculoImplement() throws RemoteException{}

    public void setRadio (double valorRadio) throws RemoteException{
        this.radio =valorRadio;
    }

    public double getArea () throws RemoteException{
        double areaCirculo =PI * ( radio * radio );
        return areaCirculo;
    }
    
}
