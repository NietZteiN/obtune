using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static long F(string text, string character) {
        return text.LastIndexOf(character);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("breakfast"), ("e")) == (2L));
    }

}
