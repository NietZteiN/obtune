using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(float float_number) {
        string number = float_number.ToString();
        int dot = number.IndexOf('.');
        if(dot != -1) {
            return number.Substring(0, dot) + '.' + number.Substring(dot + 1).PadRight(2, '0');
        }
        return number + ".00";
    }
    public static void Main(string[] args) {
    Debug.Assert(F((3.121f)).Equals(("3.121")));
    }

}
