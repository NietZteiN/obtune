using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var new_text = text.ToCharArray().ToList();
        foreach(var i in "+")
        {
            if (new_text.Contains(i))
            {
                new_text.Remove(i);
            }
        }
        return string.Join("", new_text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hbtofdeiequ")).Equals(("hbtofdeiequ")));
    }

}
