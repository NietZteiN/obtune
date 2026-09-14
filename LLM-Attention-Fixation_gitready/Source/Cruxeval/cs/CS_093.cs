using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string n) {
        int length = n.Length + 2;
        var revn = n.ToCharArray();
        string result = new string(revn);
        revn = new char[0];
        return result + new string('!', length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("iq")).Equals(("iq!!!!")));
    }

}
