using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, long l) {
        return s.PadRight((int)l, '=').TrimEnd('=');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("urecord"), (8L)).Equals(("urecord")));
    }

}
