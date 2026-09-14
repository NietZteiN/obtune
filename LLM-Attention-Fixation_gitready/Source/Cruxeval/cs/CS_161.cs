using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        var parts = text.Split(new string[] { value }, 2, StringSplitOptions.None);
        return parts[1] + parts[0];
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("difkj rinpx"), ("k")).Equals(("j rinpxdif")));
    }

}
