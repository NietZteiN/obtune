using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int s = 0;
        for (int i = 1; i < text.Length; i++)
        {
            s += text.LastIndexOf(text[i]);
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wdj")) == (3L));
    }

}
