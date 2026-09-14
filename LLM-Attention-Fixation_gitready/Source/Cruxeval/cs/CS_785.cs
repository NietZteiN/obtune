using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long n) {
        string streak = "";
        foreach (char c in n.ToString()) {
            streak += c.ToString().PadRight(int.Parse(c.ToString()) * 2);
        }
        return streak;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1L)).Equals(("1 ")));
    }

}
