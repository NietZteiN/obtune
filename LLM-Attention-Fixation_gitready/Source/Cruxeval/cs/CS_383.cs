using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string text, string chars)
    {
        var result = text.ToCharArray();
        while (Array.IndexOf(result, chars, result.Length - 3) != -1)
        {
            var resultList = new List<char>(result);
            resultList.RemoveAt(Array.LastIndexOf(result, chars, result.Length - 3));
            resultList.RemoveAt(Array.LastIndexOf(result, chars, result.Length - 3));
            result = resultList.ToArray();
        }
        return new string(result).TrimEnd('.');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ellod!p.nkyp.exa.bi.y.hain"), (".n.in.ha.y")).Equals(("ellod!p.nkyp.exa.bi.y.hain")));
    }

}
