using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, long tab) {
        return s.Replace("\t", new string(' ', (int)tab));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Join us in Hungary"), (4L)).Equals(("Join us in Hungary")));
    }

}
