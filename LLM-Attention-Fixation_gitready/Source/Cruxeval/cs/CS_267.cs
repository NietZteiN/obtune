using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long space) {
        if (space < 0) {
            return text;
        }
        return text.PadRight(text.Length / 2 + (int)space);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("sowpf"), (-7L)).Equals(("sowpf")));
    }

}
