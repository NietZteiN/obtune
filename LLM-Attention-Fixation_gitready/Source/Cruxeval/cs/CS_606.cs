using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string value) {
        List<char> ls = value.ToCharArray().ToList();
        ls.Add('N');
        ls.Add('H');
        ls.Add('I');
        ls.Add('B');
        return string.Join("", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ruam")).Equals(("ruamNHIB")));
    }

}
