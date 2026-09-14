using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    public static string F(string text, string character)
    {
        var textList = text.ToCharArray().ToList();
        for (int i = 0; i < textList.Count; i++)
        {
            if (textList[i].ToString() == character)
            {
                textList.RemoveAt(i);
                return string.Join("", textList);
            }
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("pn"), ("p")).Equals(("n")));
    }

}
