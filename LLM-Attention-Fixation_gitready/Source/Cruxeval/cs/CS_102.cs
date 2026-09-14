using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<string> names, List<string> winners) {
        List<long> ls = new List<long>();
        foreach (string name in names)
        {
            if (winners.Contains(name))
            {
                ls.Add(names.IndexOf(name));
            }
        }
        ls.Sort((a, b) => b.CompareTo(a));
        return ls;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"e", (string)"f", (string)"j", (string)"x", (string)"r", (string)"k"})), (new List<string>(new string[]{(string)"a", (string)"v", (string)"2", (string)"im", (string)"nb", (string)"vj", (string)"z"}))).SequenceEqual((new List<long>())));
    }

}
