using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long tab_size) {
        return text.Replace("\t", new string(' ', (int)tab_size));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a"), (100L)).Equals(("a")));
    }

}
