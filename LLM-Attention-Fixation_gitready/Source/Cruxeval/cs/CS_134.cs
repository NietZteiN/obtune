using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long n) {
        int t = 0;
        string b = "";
        List<int> digits = n.ToString().Select(digit => int.Parse(digit.ToString())).ToList();
        foreach (int d in digits)
        {
            if (d == 0)
            {
                t += 1;
            }
            else
            {
                break;
            }
        }
        for (int i = 0; i < t; i++)
        {
            b += "1" + "0" + "4";
        }
        b += n.ToString();
        return b;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((372359L)).Equals(("372359")));
    }

}
