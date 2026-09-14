using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        return text.Split(new[] { Environment.NewLine }, StringSplitOptions.None).Length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ncdsdfdaaa0a1cdscsk*XFd")) == (1L));
    }

}
