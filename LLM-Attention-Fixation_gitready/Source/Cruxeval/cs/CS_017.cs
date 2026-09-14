using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        return text.IndexOf(",");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("There are, no, commas, in this text")) == (9L));
    }

}
