using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text, string separator)
    {
        return string.Join(" ", text.Split(new string[] { separator }, StringSplitOptions.None));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a"), ("a")).Equals((" ")));
    }

}
