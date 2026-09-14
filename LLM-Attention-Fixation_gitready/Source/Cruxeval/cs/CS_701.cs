using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string stg, List<string> tabs) {
        foreach(var tab in tabs) {
            stg = stg.TrimEnd(tab.ToCharArray());
        }
        return stg;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("31849 let it!31849 pass!"), (new List<string>(new string[]{(string)"3", (string)"1", (string)"8", (string)" ", (string)"1", (string)"9", (string)"2", (string)"d"}))).Equals(("31849 let it!31849 pass!")));
    }

}
