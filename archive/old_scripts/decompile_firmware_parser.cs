using System;
using System.Reflection;
using System.Linq;
using System.IO;
using System.Text;

class FirmwareParserDecompiler
{
    static void Main(string[] args)
    {
        try
        {
            string exePath = "TK11.exe";
            if (!File.Exists(exePath))
            {
                Console.WriteLine("ERROR: " + exePath + " not found!");
                return;
            }

            Console.WriteLine("================================================================================");
            Console.WriteLine("TK11 FIRMWARE PARSER DECOMPILATION");
            Console.WriteLine("================================================================================\n");

            // Load the assembly
            Assembly assembly = Assembly.LoadFrom(exePath);
            Console.WriteLine("[+] Assembly loaded\n");

            // Find wfm_progress class
            Type wfmProgress = null;
            foreach (Type t in assembly.GetTypes())
            {
                if (t.Name == "wfm_progress" || t.FullName.Contains("wfm_progress"))
                {
                    wfmProgress = t;
                    break;
                }
            }

            if (wfmProgress == null)
            {
                Console.WriteLine("[-] wfm_progress class not found");
                return;
            }

            Console.WriteLine("[+] Found class: " + wfmProgress.FullName);

            // Find PareUpdataFile methods
            MethodInfo[] methods = wfmProgress.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);

            StringBuilder report = new StringBuilder();
            report.AppendLine("================================================================================");
            report.AppendLine("FIRMWARE PARSER METHODS");
            report.AppendLine("================================================================================\n");

            foreach (MethodInfo method in methods)
            {
                if (method.Name.Contains("PareUpdataFile") || method.Name.Contains("Updata") || method.Name.Contains("downloadFile"))
                {
                    Console.WriteLine("\n[+] Method: " + method.Name);
                    report.AppendLine("\n" + new string('=', 80));
                    report.AppendLine("METHOD: " + method.Name);
                    report.AppendLine(new string('=', 80));
                    report.AppendLine("Return Type: " + method.ReturnType);

                    ParameterInfo[] parameters = method.GetParameters();
                    if (parameters.Length > 0)
                    {
                        report.AppendLine("\nParameters:");
                        foreach (ParameterInfo param in parameters)
                        {
                            report.AppendLine("  - " + param.ParameterType + " " + param.Name);
                        }
                    }

                    // Get method body
                    try
                    {
                        MethodBody body = method.GetMethodBody();
                        if (body != null)
                        {
                            report.AppendLine("\nMethod Body:");
                            report.AppendLine("  IL Code Size: " + body.GetILAsByteArray().Length + " bytes");
                            report.AppendLine("  Max Stack Size: " + body.MaxStackSize);

                            // Get local variables
                            var locals = body.LocalVariables;
                            if (locals.Count > 0)
                            {
                                report.AppendLine("\n  Local Variables:");
                                foreach (var local in locals)
                                {
                                    report.AppendLine("    [" + local.LocalIndex + "] " + local.LocalType);
                                }
                            }

                            // Get IL bytes
                            byte[] il = body.GetILAsByteArray();
                            report.AppendLine("\n  IL Bytes (hex):");
                            for (int i = 0; i < Math.Min(il.Length, 500); i += 16)
                            {
                                StringBuilder hex = new StringBuilder();
                                hex.Append("    ");
                                for (int j = 0; j < 16 && i + j < il.Length; j++)
                                {
                                    hex.Append(il[i + j].ToString("X2") + " ");
                                }
                                report.AppendLine(hex.ToString());
                            }
                            if (il.Length > 500)
                            {
                                report.AppendLine("    ... (" + (il.Length - 500) + " more bytes)");
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        report.AppendLine("  Error getting method body: " + ex.Message);
                    }

                    report.AppendLine();
                }
            }

            // Save report
            string reportFile = "firmware_parser_decompilation.txt";
            File.WriteAllText(reportFile, report.ToString(), Encoding.UTF8);
            Console.WriteLine("\n[+] Full report saved to: " + reportFile);

            // Also look for constants/fields
            Console.WriteLine("\n[+] Searching for constants and fields...");
            FieldInfo[] fields = wfmProgress.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);

            Console.WriteLine("\nFields found:");
            foreach (FieldInfo field in fields)
            {
                Console.WriteLine("  - " + field.FieldType + " " + field.Name);
                if (field.IsStatic && field.IsLiteral)
                {
                    try
                    {
                        object val = field.GetRawConstantValue();
                        Console.WriteLine("    = " + val);
                    }
                    catch { }
                }
            }

            Console.WriteLine("\n[*] Analysis complete!");

        }
        catch (Exception ex)
        {
            Console.WriteLine("ERROR: " + ex.Message);
            Console.WriteLine("Stack trace: " + ex.StackTrace);
        }
    }
}
