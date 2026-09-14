using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long count) {
        for (long i = 0; i < count; i++) {
            char[] charArray = text.ToCharArray();
            Array.Reverse(charArray);
            text = new string(charArray);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("439m2670hlsw"), (3L)).Equals(("wslh0762m934")));
    }

}
