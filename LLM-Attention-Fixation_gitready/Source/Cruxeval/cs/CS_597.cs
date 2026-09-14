using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        return s.ToUpper();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Jaafodsfa SOdofj AoaFjIs  JAFasIdfSa1")).Equals(("JAAFODSFA SODOFJ AOAFJIS  JAFASIDFSA1")));
    }

}
