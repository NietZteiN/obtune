using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<List<string>> messages) {
        string phone_code = "+353";
        List<string> result = new List<string>();
        foreach(var message in messages)
        {
            message.AddRange(phone_code.ToCharArray().Select(c => c.ToString()).ToList());
            result.Add(string.Join(";", message));
        }
        return string.Join(". ", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<List<string>>(new List<string>[]{(List<string>)new List<string>(new string[]{(string)"Marie", (string)"Nelson", (string)"Oscar"})}))).Equals(("Marie;Nelson;Oscar;+;3;5;3")));
    }

}
