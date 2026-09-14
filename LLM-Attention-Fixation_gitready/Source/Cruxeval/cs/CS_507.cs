using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string search) {
        var result = text.ToLower();
        return result.IndexOf(search.ToLower());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("car hat"), ("car")) == (0L));
    }

}
