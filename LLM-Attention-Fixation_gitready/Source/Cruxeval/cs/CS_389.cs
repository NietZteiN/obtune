using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> total, string arg) {
        if (arg.GetType() == typeof(List<string>))
        {
            foreach(var e in arg.ToCharArray())
            {
                total.Add(e.ToString());
            }
        }
        else
        {
            foreach(var e in arg)
            {
                total.Add(e.ToString());
            }
        }
        return total;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"1", (string)"2", (string)"3"})), ("nammo")).SequenceEqual((new List<string>(new string[]{(string)"1", (string)"2", (string)"3", (string)"n", (string)"a", (string)"m", (string)"m", (string)"o"}))));
    }

}
