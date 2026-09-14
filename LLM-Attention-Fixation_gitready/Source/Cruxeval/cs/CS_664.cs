using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<string,string> tags) {
        string resp = "";
        foreach (var key in tags.Keys)
        {
            resp += key + " ";
        }
        return resp;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,string>(){{"3", "3"}, {"4", "5"}})).Equals(("3 4 ")));
    }

}
