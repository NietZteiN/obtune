using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string g, field;
        field = text.Replace(" ", "");
        g = text.Replace("0", " ");
        text = text.Replace("1", "i");

        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("00000000 00000000 01101100 01100101 01101110")).Equals(("00000000 00000000 0ii0ii00 0ii00i0i 0ii0iii0")));
    }

}
