using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string var) {
        if (var.All(char.IsDigit))
        {
            return "int";
        }
        else if (var.Replace(".", "").All(char.IsDigit))
        {
            return "float";
        }
        else if (var.Count(c => c == ' ') == var.Length - 1)
        {
            return "str";
        }
        else if (var.Length == 1)
        {
            return "char";
        }
        else
        {
            return "tuple";
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((" 99 777")).Equals(("tuple")));
    }

}
