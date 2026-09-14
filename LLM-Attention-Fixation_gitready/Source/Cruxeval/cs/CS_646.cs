using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long count) {
        for (long i = 0; i < count; i++)
        {
            text = new string(text.Reverse().ToArray());
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("aBc, ,SzY"), (2L)).Equals(("aBc, ,SzY")));
    }

}
