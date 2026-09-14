using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) 
    {
        int count = str.Count(c => c == ':');
        return str.Remove(str.LastIndexOf(':'), count - 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1::1")).Equals(("1:1")));
    }

}
