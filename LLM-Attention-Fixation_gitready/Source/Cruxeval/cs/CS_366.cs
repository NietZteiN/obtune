using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        string tmp = str.ToLower();
        foreach(char charac in str.ToLower())
        {
            if (tmp.Contains(charac))
            {
                tmp = tmp.Remove(tmp.IndexOf(charac), 1);
            }
        }
        return tmp;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("[ Hello ]+ Hello, World!!_ Hi")).Equals(("")));
    }

}
