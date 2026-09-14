using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        string[] s = text.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);
        return s.Length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("145\n\n12fjkjg")) == (3L));
    }

}
