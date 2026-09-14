using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text, string pref)
    {
        if (text.StartsWith(pref))
        {
            int n = pref.Length;
            string[] textParts = text.Substring(n).Split('.');
            string[] prefParts = text.Substring(0, n).Split('.');
            text = string.Join(".", textParts.Skip(1).Concat(prefParts.Take(prefParts.Length - 1)));
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("omeunhwpvr.dq"), ("omeunh")).Equals(("dq")));
    }

}
