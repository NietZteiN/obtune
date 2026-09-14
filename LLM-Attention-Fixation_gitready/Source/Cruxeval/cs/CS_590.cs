using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text)
    {
        for (int i = 10; i > 0; i--)
        {
            text = text.TrimStart(i.ToString()[0]);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("25000   $")).Equals(("5000   $")));
    }

}
