using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string chars) {
        var charsList = new List<char>(chars);
        var textList = new List<char>(text);
        var newText = textList;
        while (newText.Count > 0 && textList.Count > 0)
        {
            if (charsList.Contains(newText[0]))
            {
                newText = newText.Skip(1).ToList();
            }
            else
            {
                break;
            }
        }
        return string.Join("", newText);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("asfdellos"), ("Ta")).Equals(("sfdellos")));
    }

}
