using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string a, string split_on) {
        var t = a.Split();
        var arr = new List<char>();
        foreach (var i in t)
        {
            foreach (var j in i)
            {
                arr.Add(j);
            }
        }
        if (arr.Contains(char.Parse(split_on)))
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("booty boot-boot bootclass"), ("k")) == (false));
    }

}
