using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string x, string y) {
        var tmp = new string(y.Reverse().Select(c => c == '9' ? '0' : '9').ToArray());
        if (long.TryParse(x, out _) && long.TryParse(tmp, out _))
        {
            return x + tmp;
        }
        else
        {
            return x;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((""), ("sdasdnakjsda80")).Equals(("")));
    }

}
