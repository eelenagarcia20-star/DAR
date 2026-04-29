
public class Circulo {
    private double PI =Math.PI;
    private double radio;
    
    public Circulo(){
    }

    public void setRadio (double valorRadio){
        this.radio = valorRadio;
    }

    public double getArea (){
        double areaCirculo = PI * (radio * radio);
        return areaCirculo;
    }
}