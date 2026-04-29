import java.util.Scanner;

public class Ejemplo_circulo{

    public static void main(String[] args){
        Scanner lecuturaTeclado =new Scanner(System.in);
        System.out.print("Introduzca el radio del círculo: ");
        double radio = lecuturaTeclado.nextDouble ();
        Circulo circulo = new Circulo ();
        circulo.setRadio(radio);
        double area = circulo.getArea();
        System.out.println ("El area es : "+area); 
    }
}